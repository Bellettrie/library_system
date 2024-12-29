module.exports = {
    content: ["../../**/*.html",
        "!node_modules",
        "!../../venv/"],
    // darkMode: 'class',
    theme: {

        extend: {
            flexBasis: {
                "1/12-gap-3": "calc( 8.333333% - (1.6rem))",
                "2/12-gap-3": "calc( 16.666667% - (1.6rem))",
                "3/12-gap-3": "calc( 25% - (1.6rem))",
                "4/12-gap-3": "calc( 33.333333% - (1.6rem))",
                "5/12-gap-3": "calc( 41.666667% - (1.6rem))",
                "6/12-gap-3": "calc( 50% - (1.6rem))",
                "7/12-gap-3": "calc( 58.333333% - (1.6rem))",
                "8/12-gap-3": "calc( 66.666667% - (1.6rem))",
                "9/12-gap-3": "calc( 75% - (1.6rem))",
                "10/12-gap-3": "calc( 83.333333% - (1.6rem))",
                "11/12-gap-3": "calc( 91.666667% - (1.6rem))",
                "12/12-gap-3": "calc( 100% - (0.8rem))"
            },
            screens: {
                "md": '800px',
                "lg": '1300px',
                "xl": '1600px',
            },
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