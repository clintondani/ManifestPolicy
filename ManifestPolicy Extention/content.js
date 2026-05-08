chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "GET_TEXT") {

    function findPrivacyLink() {
      const links = document.querySelectorAll("a");
      for (let link of links) {
        const text = link.innerText.toLowerCase();
        if (text.includes("privacy")) {
          return link.href;
        }
      }
      return null;
    }

    sendResponse({
      text: document.body ? document.body.innerText : "",
      privacyLink: findPrivacyLink()
    });
  }
});
