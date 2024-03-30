using System;
using UnityEngine;

public static class WavUtility
{
    public static AudioClip ToAudioClip(byte[] wavData, int offsetSamples = 0, string name = "wav")
    {
        // Get the WAV file's header data
        int channels = BitConverter.ToInt16(wavData, 22);
        int sampleRate = BitConverter.ToInt32(wavData, 24);
        int byteRate = BitConverter.ToInt32(wavData, 28);
        int blockAlign = BitConverter.ToInt16(wavData, 32);
        int bitsPerSample = BitConverter.ToInt16(wavData, 34);
        int dataStartIndex = 44;

        // Calculate the number of audio samples
        int subchunk2Size = BitConverter.ToInt32(wavData, 40);
        int sampleCount = subchunk2Size / blockAlign;

        // Create the audio clip
        AudioClip audioClip = AudioClip.Create(name, sampleCount, channels, sampleRate, false);

        // Convert the WAV data to Unity's audio data format
        float[] audioData = new float[sampleCount];
        int offsetIndex = offsetSamples * blockAlign;
        for (int i = 0; i < sampleCount; i++)
        {
            int dataIndex = dataStartIndex + offsetIndex + (i * blockAlign);
            short sample = BitConverter.ToInt16(wavData, dataIndex);
            audioData[i] = sample / 32768f; // Convert from Int16 to [-1.0f, 1.0f]
        }

        // Set the audio data
        audioClip.SetData(audioData, 0);

        return audioClip;
    }
}
