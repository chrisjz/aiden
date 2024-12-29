using UnityEngine;
using UnityEngine.InputSystem;
using CandyCoded.env;

public class AgentMenu : MonoBehaviour
{
    public GameObject menuCanvas;
    public GameObject firstPersonCanvas;
    public GameObject playerChatCanvas;
    public PlayerInput playerInput;
    public PlayerLook playerLook;
    public GameObject sectionLog;
    public GameObject sectionControl;
    public GameObject sectionMemory;
    public GameObject sectionConfiguration;
    public GameObject sectionBackground;
    public GameObject scrollViewLogOutput;
    public GameObject scrollViewLogOutputText;
    public Vector3 toggledPositionScrollViewLogOutput;
    public Vector2 toggledSizeDeltaScrollViewLogOutput;
    public Vector2 toggledSizeDeltaScrollViewLogOutputText;
    public bool enableMenu = true;

    private bool isMenuVisible = false;
    private Vector3 originalPositionScrollViewLogOutput;
    private Vector2 originalSizeDeltaScrollViewLogOutput;
    private Vector2 originalSizeDeltaScrollViewLogOutputText;

    void Start()
    {
        // Save the original position and size of the log output GameObject
        if (scrollViewLogOutput != null)
        {
            RectTransform parentRectTransform = scrollViewLogOutput.GetComponent<RectTransform>();
            if (parentRectTransform == null)
            {
                Debug.LogError("Target log output object does not have a RectTransform.");
                return;
            }

            originalPositionScrollViewLogOutput = parentRectTransform.localPosition;
            originalSizeDeltaScrollViewLogOutput = parentRectTransform.sizeDelta;
        }
        else
        {
            Debug.LogError("Target log output object is not assigned.");
        }

        // Save the original size of the log output text GameObject
        if (scrollViewLogOutputText != null)
        {
            RectTransform childRectTransform = scrollViewLogOutputText.GetComponent<RectTransform>();
            if (childRectTransform == null)
            {
                Debug.LogError("Target log output object does not have a RectTransform.");
                return;
            }

            originalSizeDeltaScrollViewLogOutputText = childRectTransform.sizeDelta;
        }
        else
        {
            Debug.LogError("Target log output object is not assigned.");
        }
    }

    void Update()
    {
        if (!enableMenu)
        {
            return;
        }

        env.TryParseEnvironmentVariable("AUDITORY_LANGUAGE_ENABLE", out bool isAuditoryLanguageEnabled);
        env.TryParseEnvironmentVariable("VISION_ENABLE", out bool isVisionEnabled);
        env.TryParseEnvironmentVariable("VOCAL_ENABLE", out bool isVocalEnabled);
        if (Input.GetKeyDown(KeyCode.BackQuote)) // KeyCode for the tilde (~) key
        {
            isMenuVisible = !isMenuVisible;
            menuCanvas.SetActive(isMenuVisible);
            firstPersonCanvas.SetActive(!isMenuVisible);
            playerInput.enabled = !isMenuVisible;
            playerLook.enabled = !isMenuVisible;

            // Lock or unlock the cursor based on the menu state
            if (isMenuVisible)
            {
                Cursor.lockState = CursorLockMode.None; // Unlock the cursor
                Cursor.visible = true;

                playerChatCanvas.SetActive(false);
            }
            else
            {
                Cursor.lockState = CursorLockMode.Locked; // Lock the cursor
                Cursor.visible = false;
            }

            ToggleLogOutputLocation();
        }
    }

    public void OpenSectionLog()
    {
        sectionLog.SetActive(true);
        sectionControl.SetActive(false);
        sectionMemory.SetActive(false);
        sectionConfiguration.SetActive(false);

        ToggleLogOutputLocation();
    }

    public void OpenSectionControl()
    {
        sectionLog.SetActive(false);
        sectionControl.SetActive(true);
        sectionMemory.SetActive(false);
        sectionConfiguration.SetActive(false);

        ToggleLogOutputLocation();
    }

    public void OpenSectionMemory()
    {
        sectionLog.SetActive(false);
        sectionControl.SetActive(false);
        sectionMemory.SetActive(true);
        sectionConfiguration.SetActive(false);

        ToggleLogOutputLocation();
    }

    public void OpenSectionConfiguration()
    {
        sectionLog.SetActive(false);
        sectionControl.SetActive(false);
        sectionMemory.SetActive(false);
        sectionConfiguration.SetActive(true);

        ToggleLogOutputLocation();
    }

    public void ToggleLogOutputLocation()
    {
        if (scrollViewLogOutput == null || scrollViewLogOutputText == null) return;

        RectTransform parentRectTransform = scrollViewLogOutput.GetComponent<RectTransform>();
        RectTransform childRectTransform = scrollViewLogOutputText.GetComponent<RectTransform>();
        if (parentRectTransform == null || childRectTransform == null) return;

        if (isMenuVisible && sectionLog.activeSelf)
        {
            // Move and resize to toggled position and size
            parentRectTransform.localPosition = toggledPositionScrollViewLogOutput;
            parentRectTransform.sizeDelta = toggledSizeDeltaScrollViewLogOutput;
            childRectTransform.sizeDelta = toggledSizeDeltaScrollViewLogOutputText;

            sectionBackground.SetActive(false);
        }
        else
        {
            // Revert to original position and size
            parentRectTransform.localPosition = originalPositionScrollViewLogOutput;
            parentRectTransform.sizeDelta = originalSizeDeltaScrollViewLogOutput;
            childRectTransform.sizeDelta = originalSizeDeltaScrollViewLogOutputText;

            sectionBackground.SetActive(true);
        }
    }
}
