import { checkNightMode } from "ankiutils";
import type { LayoutData } from "./$types";
export const ssr = false;
export const prerender = false;

export const load: LayoutData = async () => {
    const searchParams = new URLSearchParams(window.location.search);
    const id = searchParams.get("id") ?? "";
    window.qtWidgetId = id;

    checkNightMode();
};
