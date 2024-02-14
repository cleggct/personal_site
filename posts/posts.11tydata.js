module.exports = {
	tags: [
		"posts"
	],
	"layout": "layouts/post.njk",
    eleventyComputed: {
        title: data => data.page.filePathStem.split('/').pop().split('_').map(
            (word) => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
    },
};