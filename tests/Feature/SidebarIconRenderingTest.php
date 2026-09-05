<?php

namespace Tests\Feature;

use App\Models\User;
use Illuminate\Support\Facades\Blade;
use Tests\TestCase;

class SidebarIconRenderingTest extends TestCase
{
    public function test_sidebar_renders_svg_icons_as_markup(): void
    {
        $user = new User();
        $user->forceFill([
            'id' => 1,
            'username' => 'admin',
            'full_name' => 'Administrator',
            'role' => 'admin',
        ]);
        $this->be($user);

        $html = Blade::render('<x-app-layout><p>Konten</p></x-app-layout>');

        $this->assertStringContainsString('<svg class="h-5 w-5 shrink-0"', $html);
        $this->assertStringNotContainsString('&lt;svg class=&quot;h-5 w-5 shrink-0&quot;', $html);
    }
}
