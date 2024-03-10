using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using TMPro;

public class SpeechRecognition : MonoBehaviour
{
    public TMP_InputField inputField;

    public void StartTranscription(string audioFilePath)
    {
        Debug.Log("Start transcription.");
        StartCoroutine(SendAudioFile(audioFilePath));
    }

    private IEnumerator SendAudioFile(string filePath)
    {
        byte[] audioData = System.IO.File.ReadAllBytes(filePath);

        WWWForm form = new WWWForm();
        form.AddBinaryData("file", audioData, "audio.wav", "audio/wav");

        using (UnityWebRequest www = UnityWebRequest.Post("http://localhost:8081/transcribe/", form))
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
