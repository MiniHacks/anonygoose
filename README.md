## [Anony.news](https://anony.news)
[*Devpost*](https://devpost.com/software/anony-news)

![A rather dapper goose](https://github.com/MiniHacks/anonygoose/raw/main/copy/landing_page.jpeg)

## Inspiration

In light of recent events—such as the Hong Kong protests—it is clear that privacy is more important than ever. Media exposure of events is crucial to their success but if not done correctly it puts the people involved in danger. In 2019, more than 2000 people in Hong Kong were arrested and many more were targeted by extrajudicial crackdowns due to their involvement.[1] Increasingly, authoritarian regimes are utilizing facial recognition technology to identify and oppress anyone who takes action against them.


## What is Does

**Anony.news automatically blurs protestors’ faces** to alleviate the risk of them being identified from media coverage. **The** selective **whitelist allows reporters to continue business as usual**—providing crucial exposure—while avoiding putting those around them at risk.

The core function of the platform is a real-time RTMP proxy that existing video feeds can be passed through seamlessly before being streamed on platforms such as YouTube or Twitch or broadcast to live television. As a proof of concept, the website integrates with YouTube Live but the easily-accessed RTMP URI can be used anywhere.


## Infrastructure

The frontend is **Next.js (React)** with **Chakra UI** for components. We implemented **NextAuth.js** with a **Google OAuth2 Provider** for login (including YouTube specific OAuth scoping). In addition, the **YouTube Data API (v3)** was utilized on the front-end to programmatically start streams from a given feed.

The backend was an **RTMP proxy** using **PyRTMP** as a starting point. Interestingly enough, we did not have a REST API wrapper, streaming was done directly via RTMP URIs. **FFmpeg** converted the incoming **FLV** stream into discrete frames that were then fed into our **OpenCV** face detection model, based on **OpenFace**.[2] Once faces were extracted, **normalized cross correlation** was used to ascertain similarity to whitelisted faces and the remainder were blurred. We are using an _incredibly_ cursed pipe to stdin to get raw bytes from the server to FFmpeg for rebroadcasting to the intended RTMP URI. If you’re more the visual sort, here is a picture of the architecture:

![We're big lucidchart enthusiasts](https://github.com/MiniHacks/anonygoose/raw/main/copy/backend.png)

We structured the project as a monorepo and use **Docker Compose** with **GitHub Actions** to automagically deploy to a **Digital Ocean VPS** on push. Beyond the frontend and backend, our composition also included a shared volume for (whitelist) image hosting. Originally, we had a **MongoDB** instance as well but found that it was more practical to host it via **Atlas** on **Google Cloud Platform**.


## Challenges…

This project had a prodigious amount of integration issues. Here are some fun facts, we’ll agree to pretend that these things did not cause hours of frustration:

- The YouTube data API only allows 10,000 credits worth of requests. Starting a(n empty) livestream costs 1,600. The quota can not be raised without an appeal.
- Client OAuth2 apps on GCP require verification to be published. Our best option for testing is a whitelist but that makes for a very unsatisfying demo.
- [Starting a YouTube livestream via API is an 11 step process](https://developers.google.com/youtube/v3/live/life-of-a-broadcast) (depending how you count). The code samples are from 2013.
- RTMP provides a stream of bytes rather than discrete frames. That makes complete sense but PyRTMP is built to relay and download streams, not edit them. In general, the Python tooling was abysmal but we were wed to OpenCV and not comfortable enough with C++ to consider switching languages. Thankfully, `ffmpeg` saved the day but it felt like a Stack Overflow deus ex machina more so than our own victory.
- We still have no idea how to manage requests to an RTMP server and used raw pipes (to stdin to avoid writing to disk) on both ends of the process.


## What We Learned

Jack learned that naive CV identifiers perform quite well before casting aside simplicity and elegance in exchange for OpenFace and even better results, Samyok learned that it’s nginx proxies all the way down after chaining two of them, Ritik attained suffered through Python RTMP parsing before ascending and attaining FFmpeg enlightenment and Sasha (that’s me!) touched CSS for the first time since he abused `marquee` at the young age of elevenish.

## What’s Next?

Considering professional broadcast tooling, model fine-tuning, and an endless queue of integration work.

## Citations  

Smith, T. (2019, October 22). In Hong Kong, protesters fight to stay anonymous. The Verge. Retrieved February 13, 2022, from https://www.theverge.com/2019/10/22/20926585/hong-kong-china-protest-mask-umbrella-anonymous-surveillance

Amos, B., Ludwiczuk, B., and Satyanarayanan, M. “OpenFace: A general-purpose library with face recognition library with mobile applications”  Retrieved 13 February 2022.
