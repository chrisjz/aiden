using UnityEngine;
using UnityEngine.Networking;
using System;
using System.Collections;
using TMPro;
using CandyCoded.env;
using UnityEngine.UI;
using System.IO;

public class AuditoryAmbientAPIIntegration : MonoBehaviour
{
    public TMP_Text responseText;
    public Button sendButton;

    private string apiURL;

    // Reference to the AIAudioCapture script that handles audio recording
    public AIAudioCapture audioCapture;

    private void Start()
    {
        // Check if Auditory Ambient API is enabled
        env.TryParseEnvironmentVariable("AUDITORY_AMBIENT_ENABLE", out bool isEnabled);
        if (!isEnabled)
        {
            Debug.Log("Auditory Ambient API is disabled");
            return;
        }
        else
        {
            Debug.Log("Auditory Ambient API is enabled");
        }

        // Set API URL from environment variables to point to the auditory endpoint
        if (env.TryParseEnvironmentVariable("BRAIN_API_PROTOCOL", out string protocol) &&
            env.TryParseEnvironmentVariable("BRAIN_API_HOST", out string host) &&
            env.TryParseEnvironmentVariable("BRAIN_API_PORT", out string port))
        {
            apiURL = $"{protocol}://{host}:{port}/auditory";
            Debug.Log($"Brain API URL set to: {apiURL}");
        }
        else
        {
            Debug.LogError("Missing environment variables for brain API URL.");
            return;
        }

        sendButton.onClick.AddListener(SendRequestToAuditoryAmbientAPI);
    }

    private void SendRequestToAuditoryAmbientAPI()
    {
        sendButton.interactable = false;

        // Get the last second of audio data from the audio capture component
        float[] lastSecondAudioData = audioCapture.GetLastSecondAudio();

        // Downsample to 16,000 Hz
        float[] downsampledData = DownsampleAudio(lastSecondAudioData, AudioSettings.outputSampleRate, 16000);

        // Convert downsampled audio data to WAV format
        byte[] wavData = ConvertToWav(downsampledData, 16000);

        // Convert the byte array to Base64
        string base64audio = Convert.ToBase64String(wavData);

        Debug.Log("Start auditory ambient inference.");
        StartCoroutine(StreamRequest(base64audio));
    }

    private float[] DownsampleAudio(float[] source, int sourceSampleRate, int targetSampleRate)
    {
        if (sourceSampleRate == targetSampleRate)
        {
            return source; // No need to downsample
        }

        int sampleCount = source.Length;
        int resampleCount = (int)((long)sampleCount * targetSampleRate / sourceSampleRate);

        float[] resampledData = new float[resampleCount];
        for (int i = 0; i < resampleCount; i++)
        {
            float srcIndex = (float)i * sourceSampleRate / targetSampleRate;
            int index = Mathf.FloorToInt(srcIndex);
            float frac = srcIndex - index;
            resampledData[i] = Mathf.Lerp(source[index], source[Mathf.Min(index + 1, source.Length - 1)], frac);
        }

        return resampledData;
    }

    private byte[] ConvertToWav(float[] samples, int sampleRate)
    {
        MemoryStream memoryStream = new MemoryStream();
        BinaryWriter writer = new BinaryWriter(memoryStream);

        int byteRate = sampleRate * 2;

        // WAV header
        writer.Write(System.Text.Encoding.UTF8.GetBytes("RIFF"));
        writer.Write(36 + samples.Length * 2); // File size
        writer.Write(System.Text.Encoding.UTF8.GetBytes("WAVE"));
        writer.Write(System.Text.Encoding.UTF8.GetBytes("fmt "));
        writer.Write(16); // Subchunk1 size
        writer.Write((short)1); // Audio format (PCM)
        writer.Write((short)1); // Number of channels
        writer.Write(sampleRate);
        writer.Write(byteRate);
        writer.Write((short)2); // Block align
        writer.Write((short)16); // Bits per sample

        // Data subchunk
        writer.Write(System.Text.Encoding.UTF8.GetBytes("data"));
        writer.Write(samples.Length * 2);

        // Convert samples to 16-bit PCM
        foreach (var sample in samples)
        {
            short intSample = (short)(sample * short.MaxValue);
            writer.Write(intSample);
        }

        writer.Flush();
        writer.Close();

        return memoryStream.ToArray();
    }

    private IEnumerator StreamRequest(string base64audio)
    {
        var json = JsonUtility.ToJson(new AuditoryRequest { audio = base64audio });
        var request = new UnityWebRequest(apiURL, "POST")
        {
            uploadHandler = new UploadHandlerRaw(System.Text.Encoding.UTF8.GetBytes(json)),
            downloadHandler = new DownloadHandlerBuffer()
        };
        request.SetRequestHeader("Content-Type", "application/json");

        yield return request.SendWebRequest();

        if (request.result == UnityWebRequest.Result.Success)
        {
            string responseString = request.downloadHandler.text;
            Debug.Log("Response: " + responseString);
            UpdateResponseText(responseString);
        }
        else
        {
            Debug.LogError("Error: " + request.error);
        }

        sendButton.interactable = true;
    }

    private void UpdateResponseText(string text)
    {
        responseText.text = text;
    }
}

// Define classes to match the JSON structure of the request
[Serializable]
public class AuditoryRequest
{
    public string audio;
}
