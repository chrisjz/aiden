using UnityEngine;

public class AIAudioCapture : MonoBehaviour
{
    private AudioSource audioSource;
    private int sampleRate;
    private int bufferSize = 16000; // Capture in chunks of 16,000 samples
    private float[] audioBuffer;
    private float[] accumulatedBuffer;
    private int bufferOffset = 0;

    void Start()
    {
        audioSource = gameObject.GetComponent<AudioSource>();
        sampleRate = AudioSettings.outputSampleRate;
        audioBuffer = new float[bufferSize];
        accumulatedBuffer = new float[sampleRate]; // To store 1 second of audio
    }

    void Update()
    {
        // Capture audio data in chunks of 16,000 samples
        audioSource.GetOutputData(audioBuffer, 0);

        // Copy captured data to the accumulated buffer
        int samplesToCopy = Mathf.Min(bufferSize, accumulatedBuffer.Length - bufferOffset);
        System.Array.Copy(audioBuffer, 0, accumulatedBuffer, bufferOffset, samplesToCopy);
        bufferOffset += samplesToCopy;

        // If bufferOffset reaches 1 second worth of data (48,000 samples for 48 kHz), reset
        if (bufferOffset >= accumulatedBuffer.Length)
        {
            bufferOffset = 0; // Wrap around to start overwriting old data
        }
    }

    public float[] GetLastSecondAudio()
    {
        // Return a copy of the accumulated buffer
        float[] lastSecondAudio = new float[accumulatedBuffer.Length];
        System.Array.Copy(accumulatedBuffer, lastSecondAudio, accumulatedBuffer.Length);
        return lastSecondAudio;
    }
}
