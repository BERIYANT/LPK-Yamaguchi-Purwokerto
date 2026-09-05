@props(['disabled' => false])

<input @disabled($disabled) {{ $attributes->merge(['class' => 'border-[#0b1f3a]/20 focus:border-[#d62828] focus:ring-[#d62828] rounded-xl shadow-sm']) }}>
