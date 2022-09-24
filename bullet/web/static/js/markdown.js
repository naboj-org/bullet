let md = markdownit({
	breaks:			true,
	langPrefix:		'language-',
	linkify:		true,
	typographer:	true,
	quotes:			'„“‚‘',
});
const rendered = document.getElementById("markdown-render");
const content = document.getElementById("id_content");
const render = () => rendered.innerHTML = md.render(content.value);
render();
content.addEventListener("keyup", render);
content.addEventListener("paste", render);
