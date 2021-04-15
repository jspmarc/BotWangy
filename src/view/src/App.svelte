<script>
    export let name; // deklarasi variabel bisa gini (dari main.js)
    let num = 0; // atau gini
    const up = () => {
        num++;
    };
</script>

<main>
    <h1>Hello {name}!</h1>
    <p>Visit the <a href="https://svelte.dev/tutorial">Svelte tutorial</a> to learn how to build Svelte apps.</p>
    <button on:click={up}>I've been pressed {num} times</button>
    {#if num % 15 == 0}
        <h2>foobaz</h2>
    {:else if num % 3 == 0}
        <h2>foo</h2>
    {:else if num % 5 == 0}
        <h2>baz</h2>
    {:else}
        <h2>bar</h2>
    {/if}
    {#each ['a', 'b'] as letters}
        <h2>{letters}</h2>
    {/each}
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
