<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>LPK Yamaguchi — Belajar dan Tumbuh Bersama</title>
    @viteReactRefresh
    @vite('resources/js/kage.jsx')
    <style>
        html, body, #kage-root, .shader-frame { width: 100%; height: 100%; margin: 0; }
        body { overflow: hidden; background: #fff8fb; }
    </style>
</head>
<body>
    <div id="kage-root"></div>
    <script type="text/javascript">
        (function (d, t) {
            var v = d.createElement(t), s = d.getElementsByTagName(t)[0];
            v.onload = function () {
                window.voiceflow.chat.load({
                    verify: { projectID: '6a9f8ac9038cd414022f0c49' },
                    url: 'https://general-runtime.voiceflow.com',
                    voice: {
                        url: 'https://runtime-api.voiceflow.com'
                    }
                });
            };
            v.src = 'https://cdn.voiceflow.com/widget-next/bundle.mjs';
            v.type = 'text/javascript';
            s.parentNode.insertBefore(v, s);
        })(document, 'script');
    </script>
</body>
</html>
