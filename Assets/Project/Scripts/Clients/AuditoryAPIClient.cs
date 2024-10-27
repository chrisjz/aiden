using System;
using System.Collections;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.Networking;
using CandyCoded.env;
using PimDeWitte.UnityMainThreadDispatcher;

public class AuditoryAPIClient
{
    private string apiURL;
    private AIAudioCapture audioCapture; // Reference to the AIAudioCapture script
    private bool saveCapturedAudio;

    public AuditoryAPIClient(AIAudioCapture AIAudioCapture, bool saveInput = false)
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
            apiURL = $"{protocol}://{host}:{port}/auditory/";
            Debug.Log($"Auditory endpoint URL set to: {apiURL}");
        }
        else
        {
            Debug.LogError("Missing environment variables for brain API URL.");
        }

        // Assign the AI audio capture
        audioCapture = AIAudioCapture;
        if (audioCapture == null)
        {
            Debug.LogError("No audio source was passed to AuditoryAPIClient.");
            return;
        }

        // Toggle saving captured image
        saveCapturedAudio = saveInput;
    }

    public bool IsAPIEnabled()
    {
        return !string.IsNullOrEmpty(apiURL);
    }

    public IEnumerator GetAuditoryDataCoroutine(System.Action<string> onSuccess, System.Action<string> onError)
    {
        if (string.IsNullOrEmpty(apiURL))
        {
            onError?.Invoke("Auditory API URL is not set.");
            yield break;
        }

        // Get the last second of audio data from the audio capture component
        float[] lastSecondAudioData = audioCapture.GetLastSecondAudio();

        // Downsample to 16,000 Hz
        float[] downsampledData = DownsampleAudio(lastSecondAudioData, AudioSettings.outputSampleRate, 16000);

        // Convert downsampled audio data to WAV format
        byte[] wavData = ConvertToWav(downsampledData, 16000);

        // Save the audio data if toggled on
        SaveAudioToFile(wavData, saveCapturedAudio);

        // Convert the byte array to Base64
        string base64audio = Convert.ToBase64String(wavData);

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
            try
            {
                // Deserialize the JSON response into AuditoryResponse object
                AuditoryResponse response = JsonUtility.FromJson<AuditoryResponse>(request.downloadHandler.text);

                // Format the response into a readable string
                string responseString = "Auditory API response:\n";
                foreach (var result in response.results)
                {
                    responseString += $"Class: {result.class_name}, Score: {result.score}\n";
                }

                // Print the formatted response string
                Debug.Log(responseString);

                // Extract class names from the results
                var classNames = response.results
                    .Select(result => result.class_name)
                    .ToList();

                // Join class names into a comma-separated string
                string classNamesString = string.Join(", ", classNames);

                // Return the class names string
                onSuccess?.Invoke(classNamesString);
            }
            catch (Exception ex)
            {
                onError?.Invoke("Error parsing auditory API response: " + ex.Message);
            }
        }
        else
        {
            onError?.Invoke("Auditory API request failed: " + request.error);
        }
    }

    public async Task<string> GetAuditoryDataAsync()
    {
        if (string.IsNullOrEmpty(apiURL))
        {
            Debug.LogError("Auditory API URL is not set.");
            return null;
        }

        // Get the last second of audio data from the audio capture component
        float[] lastSecondAudioData = audioCapture.GetLastSecondAudio();

        // Fetch output sample rate on the main thread
        var sampleRateTask = new TaskCompletionSource<int>();
        UnityMainThreadDispatcher.Instance().Enqueue(() =>
        {
            try
            {
                sampleRateTask.SetResult(AudioSettings.outputSampleRate);
            }
            catch (Exception ex)
            {
                sampleRateTask.SetException(ex);
            }
        });

        int sourceSampleRate = await sampleRateTask.Task;

        // Downsample to 16,000 Hz
        float[] downsampledData = DownsampleAudio(lastSecondAudioData, sourceSampleRate, 16000);

        // Convert downsampled audio data to WAV format
        byte[] wavData = ConvertToWav(downsampledData, 16000);

        // Save the audio data if toggled on
        SaveAudioToFile(wavData, saveCapturedAudio);

        // Convert the byte array to Base64
        string base64audio = Convert.ToBase64String(wavData);
        var json = JsonUtility.ToJson(new AuditoryRequest { audio = base64audio });

        // Run UnityWebRequest on the main thread and capture response
        var responseTask = new TaskCompletionSource<string>();
        UnityMainThreadDispatcher.Instance().Enqueue(() =>
        {
            var request = new UnityWebRequest(apiURL, "POST")
            {
                uploadHandler = new UploadHandlerRaw(System.Text.Encoding.UTF8.GetBytes(json)),
                downloadHandler = new DownloadHandlerBuffer()
            };
            request.SetRequestHeader("Content-Type", "application/json");

            var asyncOp = request.SendWebRequest();

            asyncOp.completed += _ =>
            {
                if (request.result == UnityWebRequest.Result.Success)
                {
                    responseTask.SetResult(request.downloadHandler.text);
                }
                else
                {
                    responseTask.SetException(new Exception("Auditory API request failed: " + request.error));
                }
            };
        });

        try
        {
            string response = await responseTask.Task;
            Debug.Log($"Auditory API response: {response}");
            return response;
        }
        catch (Exception ex)
        {
            Debug.LogError(ex.Message);
            return null;
        }
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

// Define classes to match the JSON structure of the request
[Serializable]
public class AuditoryRequest
{
    public string audio;
}

// Define classes to match the JSON structure of the response
[Serializable]
public class AuditoryResult
{
    public string class_name;
    public float score;
}

[Serializable]
public class AuditoryResponse
{
    public AuditoryResult[] results;
}
