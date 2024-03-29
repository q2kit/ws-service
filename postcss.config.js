module.exports = (ctx) => {
  return {
    plugins: {
      tailwindcss: {},
      autoprefixer: {},
      cssnano: ctx.env === "prod" ? {} : false,
    },
  };
};
