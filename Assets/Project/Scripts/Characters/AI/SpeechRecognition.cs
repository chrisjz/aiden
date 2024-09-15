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
        if (env.TryParseEnvironmentVariable("AUDITORY_LANGUAGE_API_PROTOCOL", out string protocol) &&
            env.TryParseEnvironmentVariable("AUDITORY_LANGUAGE_API_HOST", out string host) &&
            env.TryParseEnvironmentVariable("AUDITORY_LANGUAGE_API_PORT", out string port))
        {
            apiURL = $"{protocol}://{host}:{port}/asr";
            Debug.Log($"Auditory Language API URL set to: {apiURL}");
        }
        else
        {
            Debug.LogError("Missing environment variables for auditory language API URL.");
            return;
        }

        Debug.Log("Start transcription.");
        StartCoroutine(SendAudioFile(audioFilePath));
    }

    private IEnumerator SendAudioFile(string filePath)
    {
        byte[] audioData = System.IO.File.ReadAllBytes(filePath);

        WWWForm form = new WWWForm();
        form.AddBinaryData("audio_file", audioData, "audio.wav", "audio/wav");

        using (UnityWebRequest www = UnityWebRequest.Post(apiURL, form))
        {
            yield return www.SendWebRequest();

            if (www.result == UnityWebRequest.Result.Success)
            {
                string transcription = www.downloadHandler.text;
                inputField.text = transcription;
                Debug.Log("Transcription: " + transcription);
            }
            else
            {
                Debug.LogError("Error in transcription: " + www.error);
            }
        }
    }
}
