from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import re
import torch
import gradio as gr
from transformers import pipeline

text_summary = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
  
def split_text_into_chunks(text, max_length=1024):
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        if len(" ".join(current_chunk)) + len(word) + 1 > max_length:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
        current_chunk.append(word)

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def summarize_large_text(text):
    chunks = split_text_into_chunks(text)
    summarized_chunks = []

    for chunk in chunks:
        try:
            summary = text_summary(chunk, max_length=130, min_length=30, do_sample=False)
            summarized_chunks.append(summary[0]['summary_text'])
        except Exception as e:
            summarized_chunks.append(f"Error summarizing chunk: {e}")

    return " ".join(summarized_chunks)


def extract_video_id(url):
    regex = r"(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(regex, url)
    if match:
        return match.group(1)
    return None


def get_youtube_transcript(video_url):
    video_id = extract_video_id(video_url)
    if not video_id:
        return "Video ID could not be extracted."

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)

        formatter = TextFormatter()
        text_transcript = formatter.format_transcript(transcript)

        summary_text = summarize_large_text(text_transcript)

        return summary_text
    except Exception as e:
        return f"An error occurred while processing the transcript: {e}"

gr.close_all()

app = gr.Interface(
    fn=get_youtube_transcript,
    inputs=gr.Textbox(lines=2, placeholder="Enter YouTube video URL"),
    outputs=[gr.Textbox(label="Summarized text")],
    title="YT-Summarizer",
    description="Summarize YouTube video transcripts in seconds with AI. \U0001F680"
)

app.launch()
