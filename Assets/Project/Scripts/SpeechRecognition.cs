using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using TMPro;
using CandyCoded.env;

public class SpeechRecognition : MonoBehaviour
{
    public TMP_InputField inputField;

    private string apiURL;

    public void StartTranscription(string audioFilePath)
    {
        // Set API URL from environment variables
        if (env.TryParseEnvironmentVariable("AUDITORY_API_PROTOCOL", out string protocol) &&
            env.TryParseEnvironmentVariable("AUDITORY_API_HOST", out string host) &&
            env.TryParseEnvironmentVariable("AUDITORY_API_PORT", out string port))
        {
            apiURL = $"{protocol}://{host}:{port}/transcribe/";
            Debug.Log($"Auditory API URL set to: {apiURL}");
        }
        else
        {
            Debug.LogError("Missing environment variables for auditory API URL.");
            return;
        }

        Debug.Log("Start transcription.");
        StartCoroutine(SendAudioFile(audioFilePath));
    }

    private IEnumerator SendAudioFile(string filePath)
    {
        byte[] audioData = System.IO.File.ReadAllBytes(filePath);

        WWWForm form = new WWWForm();
        form.AddBinaryData("file", audioData, "audio.wav", "audio/wav");

        using (UnityWebRequest www = UnityWebRequest.Post(apiURL, form))
        {
            yield return www.SendWebRequest();

            if (www.result == UnityWebRequest.Result.Success)
            {
                Debug.Log("Transcription: " + www.downloadHandler.text);

                // Parse the JSON response
                TranscriptionResult result = JsonUtility.FromJson<TranscriptionResult>(www.downloadHandler.text);

                // Update the InputField with the transcribed text
                inputField.text = result.transcription;
            }
            else
            {
                Debug.LogError("Error in transcription: " + www.error);
            }
        }
    }
}


// Define a class to match the structure of the JSON response
[System.Serializable]
public class TranscriptionResult
{
    public string transcription;
}
