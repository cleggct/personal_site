module.exports = function(eleventyConfig) {
    // Output directory: _site

    // Copy _includes/src to _site/src
    eleventyConfig.addPassthroughCopy("src");
}