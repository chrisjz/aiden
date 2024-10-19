using System;
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UI;
using TMPro;
using CandyCoded.env;

public class PlayerChatUIController : MonoBehaviour
{
    public TMP_InputField playerInputField;
    public TMP_Text responseText;
    public Button sendButton;

    private string apiURL;
    private string modelName;

    private void Start()
    {
        sendButton.onClick.AddListener(SendMessageToAIden);
    }

    private void SendMessageToAIden()
    {
        string playerMessage = playerInputField.text;
        sendButton.interactable = false;
        responseText.text += $"<b><color=#66ff66>User</color></b>\n";
        responseText.text += $"<color=#000000>{playerMessage}</color>\n";

        Debug.Log("Send player speech to AI agent");
        sendButton.interactable = true;
    }
}
