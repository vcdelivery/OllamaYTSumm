# Ollama Youtube Video Summarizer


A simple YouTube video summarizer using a local AI Ollama server. This tool helps you quickly understand video content by providing AI-generated summaries, saving you time in deciding which videos to watch.

## Features
- 🎯 **Simple URL Input**: Just paste any YouTube video URL
- 🤖 **Multiple AI Models**: Choose from your locally installed Ollama models
- 🎭 **Customizable Tone**: Select from various summary styles:
  - Professional (default)
  - Funny
  - Brisk
  - Serious
  - Gen Z
- 📝 **Transcript Access**: View and download the full video transcript
- 📊 **Summary Generation**: Get AI-generated summaries in your chosen style
- 💾 **Download Options**: Save both transcripts and summaries as text files
- ⚙️ **Advanced Settings**: Customize the AI prompt for better results

## Technology Used
* Python
* [Ollama Server](https://ollama.com/)
* [ollama/ollama-python](https://github.com/ollama/ollama-python)
* [jdepoix/youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api/)
* [Streamlit](https://streamlit.io/)

## Install
Remember that this relies on having already a running Ollama Server.

**1. Clone the repo**
```bash
git clone https://github.com/pleabargain/OllamaYTSumm
```

**2. Install the requirements**
```bash
cd OllamaYTSumm
pip install -r requirements.txt
```

## Run the Application
```bash
python -m streamlit run main.py
```

## Using the Streamlit Interface

### Main Features
1. **URL Input**
   - Paste any YouTube video URL
   - Default example URL provided

2. **Model Selection**
   - Choose from available Ollama models
   - Models are automatically detected from your local Ollama installation

3. **Tone Selection**
   - Choose how you want your summary presented
   - Different tones for different use cases

4. **Advanced Settings**
   - Customize the AI prompt
   - Save custom prompts for later use
   - Reset to default prompt if needed

5. **Results Display**
   - Side-by-side view of transcript and summary
   - Easy-to-read format
   - Download options for both transcript and summary

## To Do 
* Work the system prompt to get the best result possible with (hopefully) the most amount of models
* Make the script asynchronous so we can activate the Stream of the response from the server, and see it real time
* Add video thumbnail and metadata display
* Add support for multiple languages
* Add summary length options (short/medium/long)
* Add support for playlist summarization

### Disclaimer
This is a forked script. I have made some changes to the original to make it work for my needs.

## Contributions
Any contributions are welcome! Here are some ways you can contribute:
- Report bugs
- Suggest new features
- Improve documentation
- Submit pull requests

## License
This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.
