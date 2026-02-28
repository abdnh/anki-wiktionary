<script lang="ts">
    import { client, type GetSupportLinksResponse } from "$lib";
    import { promiseWithResolver, Spinner } from "ankiutils";

    import { onMount } from "svelte";

    let [linksPromise, resolveLinks] = promiseWithResolver<
        GetSupportLinksResponse
    >();

    onMount(() => {
        client.getSupportLinks({}).then(resolveLinks);
    });
</script>

<div class="m-4 p-4 w-min-screen">
    {#await linksPromise}
        <Spinner />
    {:then response}
        <main class="prose prose-2xl prose-h2:text-4xl">
            <h2>Usage</h2>
            <p>
                See the <a href={response.docsPage} target="_blank">docs</a> for
                usage.
            </p>
            <h2>Changelog</h2>
            <p>
                See <a
                    href="{response.githubPage}/blob/main/CHANGELOG.md"
                    target="_blank"
                >CHANGELOG.md</a> for a list of changes.
            </p>
            <h2>Support & feature requests</h2>
            <p>
                Please post any questions, bug reports, or feature requests in
                the
                <a href={response.forumsPage} target="_blank">support page</a>
                or the <a
                    href="{response.githubPage}/issues"
                    target="_blank"
                >issue tracker</a>.
            </p>
            <p>
                If you want priority support for your feature/help request, I'm
                available for hire. Get in touch via <a
                    href="mailto:abdo@abdnh.net"
                    target="_blank"
                >email</a> or the Upwork link below.
            </p>
            <h2>Support me</h2>
            <p>Consider supporting me if you like my work:</p>
            <a
                href="https://github.com/sponsors/abdnh"
                target="_blank"
                aria-label="GitHub Sponsors link"
            ><img
                    src="/github.png"
                    alt="GitHub logo"
                    class="not-prose"
                ></a>
            <a
                href="https://www.patreon.com/abdnh"
                target="_blank"
                aria-label="Patreon link"
            ><img
                    src="/patreon.png"
                    alt="Patreon"
                    class="not-prose"
                ></a>
            <a
                href="https://www.buymeacoffee.com/abdnh"
                target="_blank"
                aria-label="Buy Me a Coffee link"
            ><img
                    src="/buymeacoffee.png"
                    alt="Buy Me A Coffee"
                    class="not-prose"
                ></a>
            <p>I'm also available for freelance add-on development:</p>
            <a
                href="https://www.upwork.com/freelancers/~01d764ac58a0eccc5c"
                target="_blank"
                aria-label="Upwork link"
            ><img
                    src="/upwork.png"
                    alt="Upwork"
                    class="not-prose"
                ></a>
        </main>
    {/await}
</div>

<style>
    @reference "tailwindcss";

    img {
        @apply h-20;
        display: inline-block;
    }
</style>
