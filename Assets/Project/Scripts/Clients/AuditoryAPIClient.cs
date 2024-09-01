using System;
using System.Collections;
using System.IO;
using UnityEngine;
using UnityEngine.Networking;
using CandyCoded.env;

public class AuditoryAPIClient
{
    private string apiURL;

    public AuditoryAPIClient()
    {
        // Check if Auditory Ambient API is enabled
        env.TryParseEnvironmentVariable("AUDITORY_AMBIENT_ENABLE", out bool isEnabled);
        if (!isEnabled)
        {
            Debug.Log("Auditory Ambient API is disabled");
            return;
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
        }
    }

    public bool IsAPIEnabled()
    {
        return !string.IsNullOrEmpty(apiURL);
    }

    public float[] DownsampleAudio(float[] source, int sourceSampleRate, int targetSampleRate)
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

    public byte[] ConvertToWav(float[] samples, int sampleRate)
    {
        using (MemoryStream memoryStream = new MemoryStream())
        using (BinaryWriter writer = new BinaryWriter(memoryStream))
        {
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
            return memoryStream.ToArray();
        }
    }

    public void SaveAudioToFile(byte[] audioData, bool saveCapturedAudio)
    {
        if (!saveCapturedAudio) return;

        string directoryPath = Path.Combine(Application.dataPath, "../Temp/CapturedSenses/Auditory");

        // Ensure directory exists
        if (!Directory.Exists(directoryPath))
        {
            Directory.CreateDirectory(directoryPath);
        }

        string timestamp = DateTime.Now.ToString("yyyyMMddHHmmssffff");
        string filePath = Path.Combine(directoryPath, $"capturedAudio_{timestamp}.wav");

        File.WriteAllBytes(filePath, audioData);
        Debug.Log($"Saved captured audio to {filePath}");
    }

    public IEnumerator SendRequestToAuditoryAPI(string base64audio, Action<string> onResponse)
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
            onResponse?.Invoke(responseString);
        }
        else
        {
            Debug.LogError("Error: " + request.error);
            onResponse?.Invoke(null);
        }
    }
}
