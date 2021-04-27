<script>
    export let name; // deklarasi variabel bisa gini (dari main.js)
    // let num = 0; // atau gini

    // let kelompok = ['Jeane', 'Josep', 'Rei'];

    // const up = () => {
    //     num++;
    // };

    // const match = () => {
    //     fetch(`./match?text=${document.getElementById('matching_text').value}&pattern=${document.getElementById('matching_pattern').value}`)
    //         .then(res => res.json())
    //         .then(res => document.getElementById('match_result').innerText = res.index_start)
    //         .catch(err => console.log(`menghangdeh: ${err}`))
    // }

    const msgerForm = get(".msger-inputarea");
    const msgerInput = get(".msger-input");
    const msgerChat = get(".msger-chat");

    const BOT_MSGS = [
        "Hi, how are you?",
        "Ohh... I can't understand what you trying to say. Sorry!",
        "I like to play games... But I don't know how to play!",
        "Sorry if my answers are not relevant. :))",
        "I feel sleepy! :("
    ];

    // Icons made by Freepik from www.flaticon.com
    const BOT_IMG = "";
    const PERSON_IMG = "";
    const BOT_NAME = "Bot Wangy";
    const PERSON_NAME = "Mahasiswa";

    msgerForm.addEventListener("submit", event => {
        event.preventDefault();

        const msgText = msgerInput.value;
        if (!msgText) return;

        appendMessage(PERSON_NAME, PERSON_IMG, "right", msgText);
        msgerInput.value = "";

        botResponse();
    });

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

    function botResponse() {
        const r = random(0, BOT_MSGS.length - 1);
        const msgText = BOT_MSGS[r];
        const delay = msgText.split(" ").length * 100;

        setTimeout(() => {
            appendMessage(BOT_NAME, BOT_IMG, "left", msgText);
        }, delay);
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

    function random(min, max) {
        return Math.floor(Math.random() * (max - min) + min);
    }
</script>

<main>
    <h1>Hello {name}!</h1>
    <h1>TEST</h1>
    <section class="msger">
        <header class="msger-header">
            <div class="msger-header-title">
                <i class="fas fa-comment-alt"></i> Bot Wangy
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
            <input type="text" class="msger-input" placeholder="Enter your message...">
            <button type="submit" class="msger-send-btn" on:click={botResponse}>Send</button>
        </form>
    </section>
</main>

<style>
    main {
        text-align: center;
        padding: 1em;
        max-width: 240px;
        margin: 0 auto;
    }

    h1 {
        color: #ff3e00;
        text-transform: uppercase;
        font-size: 4em;
        font-weight: 100;
    }

    @media (min-width: 640px) {
        main {
            max-width: none;
        }
    }
</style>
