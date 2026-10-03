/** Original vector landscape, drawn for this prototype; no external art or fonts. */
export function InkLandscape() {
  return (
    <svg
      className="ink-landscape"
      viewBox="0 0 700 410"
      fill="none"
      aria-hidden="true"
    >
      <defs>
        <linearGradient
          id="ink-fade"
          x1="350"
          y1="80"
          x2="350"
          y2="400"
          gradientUnits="userSpaceOnUse"
        >
          <stop stopColor="#346157" stopOpacity=".3" />
          <stop offset="1" stopColor="#346157" stopOpacity="0" />
        </linearGradient>
        <filter id="ink-soft">
          <feGaussianBlur stdDeviation="2.3" />
        </filter>
      </defs>
      <circle
        cx="440"
        cy="123"
        r="58"
        stroke="#ad8d56"
        strokeOpacity=".26"
        strokeWidth=".8"
      />
      <path
        d="M60 325 C115 300 139 279 166 275 C196 270 202 204 226 200 C245 191 250 156 266 155 C295 154 290 253 321 247 C350 238 364 153 385 144 C400 138 400 101 417 100 C435 105 435 215 470 231 C499 245 512 217 533 238 C558 261 587 277 634 326Z"
        fill="url(#ink-fade)"
        filter="url(#ink-soft)"
      />
      <path
        d="M110 319 C153 298 180 283 202 274 C224 265 239 256 257 277 C279 303 299 238 323 238 C346 237 365 300 389 286 C414 272 425 268 448 292 C470 314 497 278 520 288 C546 300 562 313 594 324"
        stroke="#41675c"
        strokeOpacity=".2"
        strokeWidth="1.8"
      />
      <path
        d="M266 159 C254 190 268 207 267 232 M414 106 C402 150 417 165 411 197"
        stroke="#305a50"
        strokeOpacity=".18"
      />
      <path
        d="M58 329c163-27 192 15 360-5 111-13 156-2 221 5M124 349c137-18 198 9 347-6M286 367h179M180 384h94"
        stroke="#658076"
        strokeOpacity=".23"
      />
      <path
        d="m100 307 3-39m-3 15-11-8m13 15 13-8m-10 26 12-45m-5 19 9-6"
        stroke="#31594b"
        strokeOpacity=".44"
        strokeWidth="1.6"
      />
      <path
        d="m510 69 7-3 7 3m-60-15 5-2 5 2m80 24 4-2 4 2"
        stroke="#294b40"
        strokeOpacity=".45"
      />
      <circle cx="366" cy="318" r="2" fill="#315b4f" fillOpacity=".4" />
      <path d="m363 321-6 4h20" stroke="#315b4f" strokeOpacity=".4" />
    </svg>
  );
}
