/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                primary: "#111827",
                secondary: "#4b5563",
                accent: "#9ca3af",
                dark: "#ffffff",
                light: "#ffffff",
                emerald: "#10b981", // Keep for success states
                blue: "#3b82f6",     // Keep for links
            },
        },
    },
    plugins: [],
}
