import React from 'react';
import { createRoot } from 'react-dom/client';
import { KageLandingPage } from '@designcodeio/threeui';
import '@designcodeio/threeui/style.css';

createRoot(document.getElementById('kage-root')).render(
    <div className="shader-frame">
        <KageLandingPage
            headingFont="onest"
            bodyFont="onest"
            headingWeight="400"
            bodyWeight="300"
            primaryColor="#ffffff"
            headingSize={46}
            bodySize={17}
            headingLetterSpacing={-0.012}
        />
    </div>,
);
