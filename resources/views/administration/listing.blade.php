<x-app-layout>
    <x-slot name="pageTitle">{{ $title }}</x-slot>
    <div class="mb-7"><p class="eyebrow">{{ $eyebrow }}</p><h2 class="display-title">{{ $title }}.</h2><p class="mt-2 text-sm text-black/50">Data diambil langsung dari database LMS yang sudah ada.</p></div>
    <div class="panel overflow-hidden p-0"><div class="overflow-x-auto"><table class="data-table"><thead><tr>@foreach($columns as $column)<th>{{ $column }}</th>@endforeach</tr></thead><tbody>@forelse($rows as $row)<tr>@foreach($row as $index => $value)<td>@if($index === 0)<b>{{ $value }}</b>@elseif($index === count($row)-1)<span class="status-pill">{{ $value }}</span>@else{{ $value }}@endif</td>@endforeach</tr>@empty<tr><td colspan="{{ count($columns) }}" class="empty-state">Belum ada data.</td></tr>@endforelse</tbody></table></div></div>
</x-app-layout>
