module.exports = {
  apps: [
    {
      name: "flask-murphy-api",
      script: "./server.py",
      interpreter: "python3",
      wait_ready: true,
      instances: 1,
    },
  ],
};
