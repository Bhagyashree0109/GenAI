import torch
import pyannote.audio

print("torch version:", torch.__version__)
print("pyannote.audio version:", pyannote.audio.__version__)

import matplotlib.pyplot as plt
from pyannote.audio.pipelines import SpeakerDiarization
from pyannote.core import Segment
from huggingface_hub import login

# Your Hugging Face access token
HF_AUTH_TOKEN = "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"

# Log in to Hugging Face
login(token=HF_AUTH_TOKEN)

# Load the pre-trained diarization pipeline with authentication
try:
    pipeline = SpeakerDiarization.from_pretrained("pyannote/speaker-diarization@2.1", use_auth_token=HF_AUTH_TOKEN)
except Exception as e:
    print("Error loading the model:", e)
    pipeline = None

if pipeline is not None:
    # Path to your audio file
    audio_file = "factorial.wav"

    # Perform speaker diarization
    try:
        diarization = pipeline(audio_file)
        
        # Print and plot the result
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            print(f"start={turn.start:.1f}s stop={turn.end:.1f}s speaker_{speaker}")

        # Plot the speaker segments
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            plt.plot([turn.start, turn.end], [speaker, speaker], lw=6)

        plt.xlabel("Time (s)")
        plt.ylabel("Speaker")
        plt.title("Speaker Diarization")
        plt.show()
    except Exception as e:
        print("Error during diarization:", e)
else:
    print("Failed to load the diarization pipeline.")
