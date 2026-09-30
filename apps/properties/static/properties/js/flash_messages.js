document.querySelectorAll('[data-auto-dismiss="true"]').forEach((message) => {
    window.setTimeout(() => {
        message.classList.add("is-dismissing");
        window.setTimeout(() => message.remove(), 300);
    }, 4000);
});