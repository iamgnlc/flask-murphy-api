module.exports = {
  apps: [
    {
      name: "flask-murphy-api",
      script: "./server.py",
      instances: "MAX",
    },
  ],
};
