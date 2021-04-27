<script>
    function appendMessage(name, img, side, text) {
        //   Simple solution for small apps
        const msgHTML = `
            <div class="msg ${side}-msg">
                <div class="msg-img" style="background-image: url(${img})"></div>

                <div class="msg-bubble">
                    <div class="msg-info">
                        <div class="msg-info-name">${name}</div>
                        <div class="msg-info-time">${formatDate(new Date())}</div>
                    </div>

                    <div class="msg-text">${text}</div>
                </div>
            </div>
        `;

        msgerChat.insertAdjacentHTML("beforeend", msgHTML);
        msgerChat.scrollTop += 500;
    }

    function isTextValid(msg) {
        return !(!msg || /^\s+$/.exec(msg))
    }

    function botResponse() {
        const msg = document.getElementById('msger-input').value;
        if (!isTextValid(msg)) {
            return; // do nothing
        }
        let msgText = '';
        fetch(`send_msg?msg=${msg}`, {
            redirect: "manual",
        })
        .then(res => res.json())
        .then(res => {
            msgText = res.msg.replace(/\n/g, "<br />");
        })
        .catch(err => {
            console.log(err);
            msgText = 'Maaf, aku ga paham kamu ngomong apa 😟';
        });

        setTimeout(() => {
            appendMessage(BOT_NAME, BOT_IMG, "left", msgText);
        }, 500);
    }

    // Utils
    function get(selector, root = document) {
        return root.querySelector(selector);
    }

    function formatDate(date) {
        const h = "0" + date.getHours();
        const m = "0" + date.getMinutes();

        return `${h.slice(-2)}:${m.slice(-2)}`;
    }

    // Icons made by Freepik from www.flaticon.com
    const BOT_IMG = "";
    const PERSON_IMG = "";
    const BOT_NAME = "Bot Wangy";
    const PERSON_NAME = "Mahasiswa";

    // setup messenger stuff
    let msgerForm = null;
    let msgerInput = null;
    let msgerChat = null;

    window.onload = () => {
        msgerForm = get(".msger-inputarea");
        msgerInput = get("#msger-input");
        msgerChat = get(".msger-chat");

        msgerForm.addEventListener("submit", event => {
            event.preventDefault();

            const msgText = msgerInput.value;
            if (!isTextValid(msgText)) return;

            appendMessage(PERSON_NAME, PERSON_IMG, "right", msgText);
            msgerInput.value = "";

            botResponse();
        });
    }

</script>

<main>
    <section class="msger">
        <header class="msger-header">
            <div class="msger-header-title">
                <i class="fas fa-comment-alt"></i> {BOT_NAME}
            </div>
            <div class="msger-header-options">
                <span><i class="fas fa-cog"></i></span>
            </div>
        </header>
        <div class="msger-chat">
            <div class="msg left-msg">
                <div
                    class="msg-img"
                    style="background-image: linear-gradient(to top, #f0f3fa 0%, #eef1f5 100%);">
                </div>

                <div class="msg-bubble">
                    <div class="msg-info">
                        <div class="msg-info-name">{BOT_NAME}</div>
                    </div>

                    <div class="msg-text">
                        Halo? Selamat datang di Bot Wangy! Silahkan masukkan pesan Anda!
                    </div>
                </div>
            </div>
        </div>

        <form class="msger-inputarea">
            <input type="text" id="msger-input" placeholder="Enter your message...">
            <button type="submit" class="msger-send-btn" on:click={botResponse}>➤</button>
        </form>
    </section>
</main>

<style>
    main {
        /* text-align: center; */
        padding: 0;
        /* max-width: 240px; */
        margin: 0 auto;
        height: 100%;
    }

    @media (min-width: 640px) {
        main {
            max-width: none;
        }
    }
</style>
