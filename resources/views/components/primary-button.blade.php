<button {{ $attributes->merge(['type' => 'submit', 'class' => 'inline-flex items-center px-5 py-3 bg-[#d62828] border border-transparent rounded-xl font-semibold text-xs text-white uppercase tracking-widest hover:bg-[#b82020] focus:outline-none focus:ring-2 focus:ring-[#d62828] focus:ring-offset-2 transition ease-in-out duration-150']) }}>
    {{ $slot }}
</button>
