using UnityEngine;
using System;
using System.IO;
using CandyCoded.env;
using UnityEngine.UI;

public class MicrophoneRecorder : MonoBehaviour
{
    public SpeechRecognition speechRecognition;

    public Sprite recordingSprite;
    public Sprite recordingDisabledSprite;
    public Sprite recordingHighlightedSprite;
    public Sprite recordingPressedSprite;
    public Sprite recordingSelectedSprite;

    public Sprite notRecordingSprite;
    public Sprite notRecordingDisabledSprite;
    public Sprite notRecordingHighlightedSprite;
    public Sprite notRecordingPressedSprite;
    public Sprite notRecordingSelectedSprite;

    private string microphoneName;
    private AudioClip recording;
    private bool toggleRecording = false;
    private int sampleRate = 44100;
    private int recordingLength = 10; // Length in seconds

    void Start()
    {
        // Check if Auditory Language API is enabled
        env.TryParseEnvironmentVariable("AUDITORY_LANGUAGE_ENABLE", out bool isEnabled);
        if (!isEnabled)
        {
            Debug.Log("Auditory Language API is disabled");
            return;
        }
        else
        {
            Debug.Log("Auditory Language API is enabled");
        }

        // Check if a microphone is available
        if (Microphone.devices.Length > 0)
        {
            microphoneName = Microphone.devices[0]; // Use the first available microphone
        }
        else
        {
            Debug.LogError("No microphone found");
        }
    }

    public void ToggleRecording(Button button)
    {
        Image buttonImage = button.GetComponent<Image>();

        if (toggleRecording)
        {
            StopRecordingAndSave();
            buttonImage.sprite = notRecordingSprite;

            SpriteState spriteState = new SpriteState
            {
                disabledSprite = notRecordingDisabledSprite,
                highlightedSprite = notRecordingHighlightedSprite,
                pressedSprite = notRecordingPressedSprite,
                selectedSprite = notRecordingSelectedSprite,
            };
            button.spriteState = spriteState;
        }
        else
        {
            StartRecording();
            buttonImage.sprite = recordingSprite;

            SpriteState spriteState = new SpriteState
            {
                disabledSprite = recordingDisabledSprite,
                highlightedSprite = recordingHighlightedSprite,
                pressedSprite = recordingPressedSprite,
                selectedSprite = recordingSelectedSprite,
            };
            button.spriteState = spriteState;
        }

        toggleRecording = !toggleRecording;
    }

    private void StartRecording()
    {
        // Start recording from the microphone
        Debug.Log("Start microphone recording");
        recording = Microphone.Start(microphoneName, false, recordingLength, sampleRate);
    }

    private void StopRecordingAndSave()
    {
        if (Microphone.IsRecording(microphoneName))
        {
            // Stop the recording
            Debug.Log("Stop microphone recording");
            Microphone.End(microphoneName);

            // Convert audio to 16 kHz
            AudioClip resampledClip = AudioResampler.Resample(recording, 16000);

            // Save the recording to a WAV file
            string filePath = Path.Combine(Application.persistentDataPath, "recording.wav");
            SaveWavFile(filePath, resampledClip);
            Debug.Log($"Saved recording to {filePath}");

            // Pass the file path to the SpeechRecognition class for transcription
            speechRecognition.StartTranscription(filePath);
        }
    }

    private void SaveWavFile(string filePath, AudioClip clip)
    {
        // Create the WAV file
        using (var fileStream = CreateEmptyWavFile(filePath, clip.samples * clip.channels))
        {
            ConvertAndWrite(fileStream, clip);
            WriteHeader(fileStream, clip);
        }
    }

    private FileStream CreateEmptyWavFile(string filePath, int sampleCount)
    {
        var fileStream = new FileStream(filePath, FileMode.Create);
        byte emptyByte = new byte();

        for (int i = 0; i < 44; i++) // Write empty bytes for the header
        {
            fileStream.WriteByte(emptyByte);
        }

        return fileStream;
    }

    private void ConvertAndWrite(FileStream fileStream, AudioClip clip)
    {
        var samples = new float[clip.samples * clip.channels];
        clip.GetData(samples, 0);

        Int16[] intData = new Int16[samples.Length];
        Byte[] bytesData = new Byte[samples.Length * 2];

        int rescaleFactor = 32767; // To convert float to Int16

        for (int i = 0; i < samples.Length; i++)
        {
            intData[i] = (short)(samples[i] * rescaleFactor);
            Byte[] byteArr = new Byte[2];
            byteArr = BitConverter.GetBytes(intData[i]);
            byteArr.CopyTo(bytesData, i * 2);
        }

        fileStream.Write(bytesData, 0, bytesData.Length);
    }

    private void WriteHeader(FileStream fileStream, AudioClip clip)
    {
        var hz = clip.frequency;
        var channels = clip.channels;
        var samples = clip.samples;

        fileStream.Seek(0, SeekOrigin.Begin);

        Byte[] riff = System.Text.Encoding.UTF8.GetBytes("RIFF");
        fileStream.Write(riff, 0, 4);

        Byte[] chunkSize = BitConverter.GetBytes(fileStream.Length - 8);
        fileStream.Write(chunkSize, 0, 4);

        Byte[] wave = System.Text.Encoding.UTF8.GetBytes("WAVE");
        fileStream.Write(wave, 0, 4);

        Byte[] fmt = System.Text.Encoding.UTF8.GetBytes("fmt ");
        fileStream.Write(fmt, 0, 4);

        Byte[] subChunk1 = BitConverter.GetBytes(16);
        fileStream.Write(subChunk1, 0, 4);

        UInt16 one = 1;

        Byte[] audioFormat = BitConverter.GetBytes(one);
        fileStream.Write(audioFormat, 0, 2);

        Byte[] numChannels = BitConverter.GetBytes(channels);
        fileStream.Write(numChannels, 0, 2);

        Byte[] sampleRate = BitConverter.GetBytes(hz);
        fileStream.Write(sampleRate, 0, 4);

        Byte[] byteRate = BitConverter.GetBytes(hz * channels * 2); // sampleRate * bytesPerSample*number of channels, here 16 bit stereo sound
        fileStream.Write(byteRate, 0, 4);

        UInt16 blockAlign = (ushort)(channels * 2);
        fileStream.Write(BitConverter.GetBytes(blockAlign), 0, 2);

        UInt16 bps = 16;
        Byte[] bitsPerSample = BitConverter.GetBytes(bps);
        fileStream.Write(bitsPerSample, 0, 2);

        Byte[] datastring = System.Text.Encoding.UTF8.GetBytes("data");
        fileStream.Write(datastring, 0, 4);

        Byte[] subChunk2 = BitConverter.GetBytes(samples * channels * 2);
        fileStream.Write(subChunk2, 0, 4);

        // Now the header is complete, and the data can be written from ConvertAndWrite
    }
}
