using System.Collections;
using UnityEngine;
using UnityEngine.Networking;
using TMPro;
using CandyCoded.env;

public class TextToSpeech : MonoBehaviour
{
    public TMP_Text requestText;

    private string apiURL;

    public void SynthesizeAndPlay()
    {
        // Set API URL from environment variables
        if (env.TryParseEnvironmentVariable("VOCAL_API_PROTOCOL", out string protocol) &&
            env.TryParseEnvironmentVariable("VOCAL_API_HOST", out string host) &&
            env.TryParseEnvironmentVariable("VOCAL_API_PORT", out string port))
        {
            apiURL = $"{protocol}://{host}:{port}/synthesize/";
            Debug.Log($"Vocal API URL set to: {apiURL}");
        }
        else
        {
            Debug.LogError("Missing environment variables for vocal API URL.");
            return;
        }

        Debug.Log("Start speech synthesis.");
        StartCoroutine(SynthesizeSpeech(requestText.text));
    }

    private IEnumerator SynthesizeSpeech(string text)
    {
        WWWForm form = new WWWForm();
        form.AddField("text", text);

        using (UnityWebRequest www = UnityWebRequest.Post(apiURL, form))
        {
            www.SetRequestHeader("Content-Type", "application/x-www-form-urlencoded");

            yield return www.SendWebRequest();

            if (www.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError(www.error);
            }
            else
            {
                // Load the audio data into an AudioClip
                AudioClip audioClip = WavUtility.ToAudioClip(www.downloadHandler.data);
                if (audioClip == null)
                {
                    Debug.LogError("Failed to convert response data to AudioClip.");
                }
                else
                {
                    AudioSource audioSource = gameObject.AddComponent<AudioSource>();
                    audioSource.clip = audioClip;
                    audioSource.Play();
                }
            }
        }
    }
}
