import streamlit as st
import time
from ollama import Client
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import requests
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# YOUR OLLAMA SERVER
AI = Client(host='http://localhost:11434/')

# Set page config
st.set_page_config(
    page_title="YouTube Video Summarizer",
    page_icon="🎥",
    layout="wide"
)

def getVideoID(url) -> str:
    """
    This function gets the video id from the url provided by the user.
    Handles different YouTube URL formats.
    """
    if not url:
        return None
    # Handle different YouTube URL patterns
    if "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    elif "v=" in url:
        return url.split("v=")[1].split("&")[0]
    else:
        raise ValueError("Invalid YouTube URL format")

def get_transcription(video_id) -> dict:
    """
    Gets the transcript of the video directly from Youtube (default=en).
    """
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Convert transcript list to readable text
        full_transcript = ""
        for entry in transcript:
            full_transcript += entry['text'] + "\n"
        
        return full_transcript
    except Exception as e:
        raise Exception(f"Error getting transcript: {str(e)}")

def get_video_title(video_id) -> str:
    """
    Gets the title of the YouTube video.
    Falls back to video ID if title cannot be retrieved.
    """
    try:
        url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()['title']
    except Exception as e:
        st.warning(f"Could not get video title: {e}")
    return video_id

def getAvailableModels() -> dict:
    """
    Returns a dictionary with the list of available models installed in the Ollama server
    """
    list = AI.list()
    return list

def askOllama(transcript: str, usrModel: str, selected_tone: str, custom_prompt: str = None) -> dict:
    """
    Sends the transcript to the ollama ai server and gets a JSON response.
    
    Args:
        transcript (str): The video transcript
        usrModel (str): The AI model to use
        selected_tone (str): The tone for the summary
        custom_prompt (str, optional): Custom system prompt. Defaults to None.
    
    Returns:
        dict: The AI response containing the summary
    """
    try:
        # Use custom prompt if provided, otherwise use default
        system_prompt = custom_prompt if custom_prompt else create_default_prompt(selected_tone)
        logger.info(f"Using model: {usrModel}")
        logger.info(f"Using tone: {selected_tone}")
        
        response = AI.chat(
            model=usrModel,
            messages=[{
                'role': 'system',
                'content': system_prompt
            },
            {
                'role': 'user',
                'content': 'Transcript: ' + str(transcript)
            }],
        )
        
        if not response:
            logger.error("Received empty response from Ollama")
            raise Exception("Empty response from AI model")
            
        logger.info("Successfully generated summary")
        return response
        
    except Exception as e:
        logger.error(f"Error in askOllama: {str(e)}")
        st.error(f"Error generating summary: {str(e)}")
        return None

def create_default_prompt(selected_tone):
    """
    Creates the default system prompt with the selected tone
    """
    return (f'You are a summarizing assistant responsible for analyzing the content of YouTube videos. '
            f'{selected_tone} '
            f'The user will feed you transcriptions but you should always refer to the content in your response as "the video". '
            f'Focus on accurately summarizing the main points and key details of the videos. '
            f'Do not comment on the style of the video (e.g., whether it is a voiceover or conversational). '
            f'Do never mention or imply the existence of text, transcription, or any written format. '
            f'Use phrases like "The video discusses..." or "According to the video...". '
            f'Strive to be the best summarizer possible, providing clear, and informative summaries that exclusively reference the video content.')

def main():
    try:
        logger.info("Starting application")
        st.title("YouTube Video Summarizer")
        st.subheader("Powered by AI 🤖")
        
        # Sidebar for model and tone selection
        with st.sidebar:
            st.header("Settings")
            
            # Get available models
            try:
                logger.info("Fetching available models from Ollama")
                availableModels = getAvailableModels()
                model_names = [each['name'] for each in availableModels['models']]
                selected_model = st.selectbox(
                    "Choose AI Model",
                    model_names,
                    index=0
                )
                logger.info(f"Available models: {model_names}")
            except Exception as e:
                logger.error(f"Error loading models: {str(e)}")
                st.error("⚠️ Error loading AI models")
                st.error("Please make sure Ollama is running on http://localhost:11434/")
                return
            
            # Tone selection
            tone_options = {
                "Professional": "Use a professional and formal tone.",
                "Funny": "Be humorous and entertaining in your summary.",
                "Brisk": "Be concise and to-the-point.",
                "Serious": "Maintain a serious and analytical tone.",
                "Gen Z": "Use Gen Z slang and casual language, including modern internet expressions."
            }
            selected_tone = st.selectbox(
                "Select Summary Tone",
                options=list(tone_options.keys()),
                index=0
            )
            
            # Add prompt editing section in sidebar
            st.header("Advanced Settings")
            with st.expander("🔧 Customize AI Prompt"):
                st.info("Here you can customize the instructions given to the AI model.")
                
                st.markdown("""
                    ### Prompt Variables:
                    - `{selected_tone}`: Will be replaced with your tone selection
                    
                    ### Tips:
                    - Keep instructions clear and specific
                    - Use natural language
                    - Maintain the video-centric language
                    - Avoid mentioning transcripts or text
                    """)
                
                default_prompt = create_default_prompt(tone_options[selected_tone])
                custom_prompt = st.text_area(
                    "System Prompt",
                    value=default_prompt,
                    height=300,
                    help="Edit these instructions to customize how the AI processes the video"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Reset Prompt", help="Restore the default prompt"):
                        custom_prompt = default_prompt
                with col2:
                    st.download_button(
                        "Save Prompt",
                        custom_prompt,
                        file_name="custom_prompt.txt",
                        mime="text/plain",
                        help="Save your custom prompt for later use"
                    )

        # Main content area
        default_url = "https://youtu.be/UGMmYesxhHk"
        url = st.text_input("YouTube Video URL", value=default_url)
        
        if st.button("Generate Summary"):
            if url:
                try:
                    with st.spinner("Processing video..."):
                        # Get video details
                        logger.info(f"Processing URL: {url}")
                        video_id = getVideoID(url)
                        if not video_id:
                            logger.error("Could not extract video ID from URL")
                            st.error("Could not extract video ID from URL")
                            return
                            
                        video_title = get_video_title(video_id)
                        logger.info(f"Video title: {video_title}")
                        
                        # Create columns for transcript and summary
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("Transcript")
                            try:
                                transcript = get_transcription(video_id)
                                if transcript:
                                    st.text_area("Video Transcript", transcript, height=400)
                                    
                                    # Download transcript button
                                    st.download_button(
                                        label="Download Transcript",
                                        data=transcript,
                                        file_name=f"{video_title}_transcript.txt",
                                        mime="text/plain",
                                        help="Save the transcript to your computer"
                                    )
                                    logger.info("Successfully retrieved and displayed transcript")
                                else:
                                    logger.error("No transcript available")
                                    st.error("No transcript available for this video")
                            except Exception as e:
                                logger.error(f"Error getting transcript: {str(e)}")
                                st.error(f"Error getting transcript: {str(e)}")
                        
                        with col2:
                            st.subheader("Summary")
                            if transcript:  # Only proceed if we have a transcript
                                logger.info("Generating summary...")
                                summary = askOllama(
                                    transcript=transcript,
                                    usrModel=selected_model,
                                    selected_tone=tone_options[selected_tone],
                                    custom_prompt=custom_prompt
                                )
                                
                                if summary and 'message' in summary and 'content' in summary['message']:
                                    summary_text = summary['message']['content']
                                    st.text_area("Video Summary", summary_text, height=400)
                                    
                                    # Download summary button
                                    st.download_button(
                                        label="Download Summary",
                                        data=summary_text,
                                        file_name=f"{video_title}_summary.txt",
                                        mime="text/plain",
                                        help="Save the summary to your computer"
                                    )
                                    logger.info("Successfully generated and displayed summary")
                                else:
                                    logger.error("Failed to generate summary")
                                    st.error("Failed to generate summary")
                            
                except Exception as e:
                    logger.error(f"An error occurred: {str(e)}")
                    st.error(f"An error occurred: {str(e)}")
            else:
                logger.warning("No URL provided")
                st.warning("Please enter a YouTube URL")

    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        st.error("An unexpected error occurred. Please check the console for details.")

if __name__ == "__main__":
    main()