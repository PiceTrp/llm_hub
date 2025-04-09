#!/usr/bin/env python3
"""
YouTube Transcript Extractor and Thai Translator using LangChain and Gemini
This script extracts transcripts from a YouTube video and uses LangChain with Gemini
to translate them to Thai while preserving speaker information.
"""

import os
import re
import argparse
from typing import List, Dict, Any, Optional
from youtube_transcript_api import YouTubeTranscriptApi
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough

def extract_youtube_id(url: str) -> str:
    """Extract YouTube video ID from URL."""
    if "youtu.be" in url:
        return url.split("/")[-1]
    elif "youtube.com" in url:
        if "v=" in url:
            return url.split("v=")[1].split("&")[0]
    return url  # If already an ID

def get_youtube_transcript(video_url: str) -> Optional[List[Dict[str, Any]]]:
    """Get transcript from YouTube video."""
    video_id = extract_youtube_id(video_url)
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript_list
    except Exception as e:
        print(f"Error extracting transcript: {e}")
        return None

def format_transcript(transcript_list: List[Dict[str, Any]]) -> str:
    """Format transcript with timestamps and text."""
    if not transcript_list:
        return "No transcript available."

    formatted_text = ""
    for item in transcript_list:
        start_time = format_time(item['start'])
        text = item['text']
        formatted_text += f"[{start_time}] {text}\n"

    return formatted_text

def format_time(seconds: float) -> str:
    """Format seconds to MM:SS format."""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def preprocess_transcript(transcript_list: List[Dict[str, Any]]) -> str:
    """
    Convert transcript to a format that can be processed by LLM.
    Attempt basic speaker identification by line breaks and patterns.
    """
    full_text = ""
    for item in transcript_list:
        full_text += item['text'] + " "

    # Basic cleaning
    full_text = full_text.replace("\n", " ").strip()

    # Try to identify speakers with basic pattern matching
    # This is simplified and would need more sophisticated NLP for accuracy
    speaker_patterns = [
        r"((?:Man|Woman|Speaker \d+|Male|Female|Host|Guest|Interviewer|Interviewee|Narrator|Person \d+)\s*:)",
        r"(\b[A-Z][a-z]+\s*:)"  # Potential names followed by colon
    ]

    for pattern in speaker_patterns:
        if re.search(pattern, full_text):
            # Split by speaker indicators and reassemble with proper formatting
            segments = re.split(pattern, full_text)
            if segments[0].strip():  # If text before first speaker
                formatted = "Speaker: " + segments[0].strip() + "\n"
            else:
                formatted = ""

            for i in range(1, len(segments), 2):
                if i+1 < len(segments):
                    speaker = segments[i].strip()
                    text = segments[i+1].strip()
                    formatted += f"{speaker} {text}\n"

            return formatted

    # If no speaker patterns found, combine all text
    return "Speaker: " + full_text

# def setup_translation_chain(model):
#     """Set up LangChain for translation."""

#     # Create the prompt template for translation
#     prompt = ChatPromptTemplate.from_messages([
#         ("system", """You are a professional translator specializing in English to Thai translation.
#         Your task is to translate the provided English transcript to Thai while maintaining the same format
#         and preserving speaker indications.

#         Guidelines:
#         1. Maintain all speaker labels (like "Man:", "Woman:", "Speaker:", etc.)
#         2. Keep the conversational style and tone of the original
#         3. Preserve the structure of the transcript
#         4. Make the translation sound natural in Thai
#         5. If speaker labels are not present, keep the general format of the transcript

#         Respond ONLY with the translated Thai text, keeping the same structure as the input.
#         Do not include explanations or notes about the translation process.
#         """),
#         ("human", "{transcript}")
#     ])

#     # Create the chain
#     chain = (
#         {"transcript": RunnablePassthrough()}
#         | prompt
#         | model
#         | StrOutputParser()
#     )

#     return chain

def setup_translation_chain(model):
    """Set up LangChain for translation using a sequential approach."""

    # Step 1: Format transcript into proper sentences while preserving speaker info
    format_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert in processing speech transcripts.
        Your task is to take the raw transcript input and organize it into proper sentences
        while preserving all speaker information.

        Guidelines:
        1. Maintain all speaker labels (like "Man:", "Woman:", "Speaker:", etc.)
        2. Fix any sentence fragments or incomplete thoughts
        3. Group related content by the same speaker
        4. Keep timestamps if present
        5. Ensure proper punctuation and capitalization

        Format your response as a well-structured transcript with clear speaker indicators.
        """),
        ("human", "{transcript}")
    ])

    format_chain = (
        {"transcript": RunnablePassthrough()}
        | format_prompt
        | model
        | StrOutputParser()
    )

    # Step 2: Translate the formatted transcript to Thai
    translate_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a professional translator specializing in English to Thai translation.
        Your task is to translate the provided transcript to Thai while maintaining the exact format
        and preserving all speaker indications.

        Guidelines:
        1. Keep all speaker labels exactly as they appear (like "Man:", "Woman:", "Speaker:", etc.)
        2. Maintain the same paragraph breaks and transcript structure
        3. Preserve any timestamps or technical markers
        4. Make the translation sound natural and conversational in Thai
        5. Do not add or remove any content

        Respond ONLY with the translated Thai text, keeping the identical structure as the input.
        """),
        ("human", "{formatted_transcript}")
    ])

    translate_chain = (
        {"formatted_transcript": RunnablePassthrough()}
        | translate_prompt
        | model
        | StrOutputParser()
    )

    # Alternative way to define the sequential chain
    sequential_chain = format_chain | translate_chain

    return sequential_chain

def main(youtube_url: str):
    """Main function to run the script."""
    print(f"Extracting transcript from: {youtube_url}")

    # Extract transcript
    transcript_list = get_youtube_transcript(youtube_url)
    if not transcript_list:
        return "Failed to extract transcript."

    # Format and preprocess transcript for LLM
    formatted_transcript = format_transcript(transcript_list)
    preprocessed_transcript = preprocess_transcript(transcript_list)

    print("\n=== EXTRACTED TRANSCRIPT ===\n")
    print(formatted_transcript)
    print(preprocessed_transcript)

    # Initialize the Gemini model
    model = init_chat_model("gemini-2.0-flash-001", model_provider="google_vertexai")

    # Set up and run the translation chain
    translation_chain = setup_translation_chain(model)
    translated_text = translation_chain.invoke(preprocessed_transcript)

    print("\n=== THAI TRANSLATION ===\n")
    print(translated_text)

    return {
        "original": preprocessed_transcript,
        "thai": translated_text
    }


# Replace the main block at the bottom with this:
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract YouTube transcript and translate to Thai")
    parser.add_argument("--youtube_url", type=str, required=True, help="YouTube URL to extract transcript from")
    args = parser.parse_args()

    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    # Ensure GOOGLE_APPLICATION_CREDENTIALS is set
    print(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])

    # Run the main function with the provided YouTube URL
    result = main(args.youtube_url)
