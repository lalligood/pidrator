## Genesis ##
I was looking for a reason to get my hands on a Raspberry Pi, but I wanted a reason--a purpose--for getting one. As I've already tried my hand at Arduino & got bored/complacement with making inevitably increasing more complex LED circuits, I wanted to do something completely different, and dare I say *actually useful*.

It was around that same time that I got a food dehydrator. Also it just so happened that I'd been making more & more meals with a slow cooker (aka crock pot) but sometimes they were coming out overcooked when I got home after turning it on as I left home in the morning.

I thought: "It sure would be nice if I had a way that I could control either of those appliances..." Then there was a flash of inspiration, an order was placed, and an idea was born! (The other option was to replace 2 perfectly good, working applicances with much more expensive & still not quite as functional appliances.)

## Getting the hardware ##
If I was going to pull this off, I would need a wifi adapter, high temp waterproof DS18B20 Digital temperature sensor, & a Powertail to turn on/off the dehydrator or slow cooker.

Both the Powertail & temp sensor use the RPi.GPIO class for functionality. In less than 20 lines of Python, it's trivial to enable, turn on/off, & read from both pieces of equipment. And sure if I wanted to "just" do those things, it would have only taken a few minutes...but I have bigger ideas in mind!

## Ambitions or Too Ambitious? ##
Among the crazy ideas I have been contemplating:

1. I work with databases for a living. So I figured if I'm going to configure the RPi to control the cooking process, why not record the data while I'm at it? I envisioned tracking the rise & fall of the cooking temperatures, determining the optimal cooking time for everything I like to make, and more. The easiest way to do this (I thought) is with a database. The project was expanded to account for this.
2. Sure I could access the RPi remotely via SSH--and I'm very comfortable doing that--but what if I wanted to monitor--or even control--the cooking process through a webpage?! Yup, gotta build a HTML front end to control my ever expanding scope...
3. And if I have a web front end, that means I'll need graphics. And some of those graphics could lead to making charts. So we need charts.
4. But controlling it should be *easy*. Dead frickin' simple to use. That means menus. Menus that allow you to create a new job (read: cooking schedule), pick a previous job, and modify the current job. Menus that make it very easy to configure & run the appliances.
5. Be smart. With the slow cooker, most dishes are usually cooked in 8 hours or less. But I leave the house in the morning & don't get back home for closer to 10 hours later most days. So I need something that will effectively turn off after 8 hours (or however long I want it to) but maybe monitor the temperature & turn itself back on long enough to maintain a certain (warm) temperature after that... And with the dehydrator, you need to rotate the trays so that the food on the top doesn't overdry while the food on the bottom tray needs to go longer. So alerting me every once in a while to rotate the trays would be very helpful too.
6. If all that wasn't enough, I happen to have a 16x2 LCD with buttons that I've contemplated adding to the RPi. So instead of havinng to use my web browser or a terminal session to start/monitor/stop a cooking job, I could do it all from the "front panel" of the RPi. Here is where I begin to question my own sanity though...

## So Let's Get to Work, Shall We? ##
