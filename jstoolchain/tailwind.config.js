module.exports = {
    content: ["../**/*.html"],
    darkMode: 'class',
    theme: {
        extend: {},
    },
    prefix: 'tw-',
    plugins: [require("@tailwindcss/typography"), require(getDaisyUI())],

    daisyui: {
        styled: true,
        base: true,
        utils: true,
        logs: true,
        rtl: false,
        prefix: "",
        themes: ["light"],
    },
}

function getDaisyUI() {
    return "daisyui";
}