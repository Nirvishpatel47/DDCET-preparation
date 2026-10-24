const fs = require('fs');

// Load KaTeX and Marked
const katexCode = fs.readFileSync('static/libs/katex.min.js', 'utf8');
const markedCode = fs.readFileSync('static/libs/marked.min.js', 'utf8');

// Evaluate in global context
eval(katexCode);
eval(markedCode);

const App = {
    renderContent: function (text) {
        if (!text) return '';
        let str = String(text);

        const mathRegex = /(\$\$[\s\S]*?\$\$|\\\[[\s\S]*?\\\]|(?<!\\)\$((?:\\\$|[^\$])+?)\$|\\\([\s\S]*?\\\))/g;

        let lastIndex = 0;
        let htmlResult = '';
        let match;

        while ((match = mathRegex.exec(str)) !== null) {
            const matchIndex = match.index;
            const fullMatch = match[0];

            if (matchIndex > lastIndex) {
                const textChunk = str.substring(lastIndex, matchIndex);
                htmlResult += this.renderMarkdownOnly(textChunk);
            }

            let isDisplay = false;
            let mathCode = '';

            if (fullMatch.startsWith('$$') && fullMatch.endsWith('$$')) {
                isDisplay = true;
                mathCode = fullMatch.slice(2, -2).trim();
            } else if (fullMatch.startsWith('\\[') && fullMatch.endsWith('\\]')) {
                isDisplay = true;
                mathCode = fullMatch.slice(2, -2).trim();
            } else if (fullMatch.startsWith('\\(') && fullMatch.endsWith('\\)')) {
                isDisplay = false;
                mathCode = fullMatch.slice(2, -2).trim();
            } else if (fullMatch.startsWith('$') && fullMatch.endsWith('$')) {
                isDisplay = false;
                mathCode = fullMatch.slice(1, -1).trim();
            }

            mathCode = mathCode.replace(/\\\$/g, '$');

            if (typeof katex !== 'undefined') {
                try {
                    htmlResult += katex.renderToString(mathCode, {
                        displayMode: isDisplay,
                        throwOnError: false
                    });
                } catch (e) {
                    htmlResult += isDisplay
                        ? `<div class="katex-display">${this.escapeHtml(mathCode)}</div>`
                        : `<span class="math-inline">${this.escapeHtml(mathCode)}</span>`;
                }
            } else {
                htmlResult += isDisplay
                    ? `<div class="katex-display">${this.escapeHtml(mathCode)}</div>`
                    : `<span class="math-inline">${this.escapeHtml(mathCode)}</span>`;
            }

            lastIndex = matchIndex + fullMatch.length;
        }

        if (lastIndex < str.length) {
            const remainingText = str.substring(lastIndex);
            htmlResult += this.renderMarkdownOnly(remainingText);
        }

        return htmlResult;
    },

    renderMarkdownOnly: function (text) {
        if (!text) return '';
        if (typeof marked !== 'undefined' && marked.parseInline) {
            if (text.includes('\n\n') || text.trim().startsWith('#') || text.trim().startsWith('-') || text.trim().startsWith('*')) {
                return marked.parse(text, { breaks: true, gfm: true });
            }
            return marked.parseInline(text, { breaks: true, gfm: true });
        }
        return this.escapeHtml(text)
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
    },

    escapeHtml: function (str) {
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
};

const input = "If $\\begin{vmatrix} x & 2 \\\\ 8 & x \\end{vmatrix} = 0$, what is the value of $x$?";
const output = App.renderContent(input);

console.log("Input:", input);
console.log("Contains MATH_INL?", output.includes("MATH_INL"));
console.log("Contains katex class?", output.includes("katex"));
console.log("Contains vmatrix/matrix elements?", output.includes("vmatrix") || output.includes("mtable") || output.includes("left-delim") || output.includes("vline"));
console.log("\nOutput preview:\n", output.substring(0, 300));
