module.exports = {
    content: ["../../**/*.html",
    "!**/node_modules",
    "!../../venv/"],
    // darkMode: 'class',
    theme: {
        extend: {
            colors: {
                belleyellow: "#f7ec55",
                bellered: "#c14d00",
            }
        }
    },
    //     extend: {},
    // },
    darkMode: 'true',
    plugins: [require("@tailwindcss/typography"), require(getDaisyUI())],

    daisyui: {
        styled: true,
        base: true,
        utils: true,
        logs: true,
        rtl: false,
        prefix: "",
        themes: [
            {
                mytheme: {
                    "primary": "#a991f7",
                    "secondary": "#f6d860",
                    "accent": "#37cdbe",
                    "neutral": "#3d4451",
                    "base-100": "#ffffff",
                },
            },
            {
                mytheme: {
                    "primary": "#a991f7",
                    "secondary": "#f6d860",
                    "accent": "#37cdbe",
                    "neutral": "#3d4451",
                    "base-100": "#ffffff",
                },
            },
        ],
    },
}

function getDaisyUI() {
    return "daisyui";
}