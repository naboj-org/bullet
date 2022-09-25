let md = markdownit({
	html:			 true,
	langPrefix:		 'language-',
	typographer:	 true,
	quotes:			 '„“‚‘',
}).use(markdownitFootnote).use(markdownitAbbr).use(markdownitAdmon).use(markdownItAttrs, {
  leftDelimiter:     '{:',
  rightDelimiter:    '}',
  allowedAttributes: []  // empty array = all attributes are allowed
});

const easyMDE = new EasyMDE({
	element: document.getElementById('id_content'),
	previewClass: ["prose", "max-w-none", "editor-preview"],
	tabSize: 4,
	spellChecker: false,
	inputStyle: "contenteditable",
	showIcons: ["code", "table", "undo", "redo"],
	hideIcons: ["image"],
	shortcuts: {
		drawTable: "Cmd-Alt-T",
		undo: "Cmd-Z",
		redo: "Cmd-Y",
    },
	previewRender: (a) => md.render(a),
});
