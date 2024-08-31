using System.Linq;
using UnityEngine;
using System.Collections.Generic;

public class AIAudioCapture : MonoBehaviour
{
    public float detectionRadius = 10f; // Radius to detect AudioSources
    public LayerMask audioSourceLayer;  // Layer on which AudioSources are placed
    private int sampleRate;
    private int bufferSize = 16000; // Capture in chunks of 16,000 samples
    private float[] audioBuffer;
    private float[] accumulatedBuffer;
    private int bufferOffset = 0;

    void Start()
    {
        sampleRate = AudioSettings.outputSampleRate;
        audioBuffer = new float[bufferSize];
        accumulatedBuffer = new float[sampleRate]; // To store 1 second of audio
    }

    void Update()
    {
        // Detect all AudioSources within the specified radius
        Collider[] hitColliders = Physics.OverlapSphere(transform.position, detectionRadius, audioSourceLayer);
        List<AudioSource> audioSources = new List<AudioSource>();

        foreach (Collider hitCollider in hitColliders)
        {
            AudioSource source = hitCollider.GetComponent<AudioSource>();
            if (source != null && source.isPlaying)
            {
                audioSources.Add(source);
            }
        }

        // Aggregate audio from all detected AudioSources
        foreach (AudioSource source in audioSources)
        {
            CaptureAudioFromSource(source);
        }
    }

    private void CaptureAudioFromSource(AudioSource source)
    {
        // Capture audio data from the AudioSource
        source.GetOutputData(audioBuffer, 0);

        // Copy captured data to the accumulated buffer
        int samplesToCopy = Mathf.Min(bufferSize, accumulatedBuffer.Length - bufferOffset);
        System.Array.Copy(audioBuffer, 0, accumulatedBuffer, bufferOffset, samplesToCopy);
        bufferOffset += samplesToCopy;

        // If bufferOffset reaches 1 second worth of data (sampleRate samples), reset
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

    void OnDrawGizmosSelected()
    {
        // Draw the detection radius in the editor
        Gizmos.color = Color.cyan;
        Gizmos.DrawWireSphere(transform.position, detectionRadius);
    }
}
