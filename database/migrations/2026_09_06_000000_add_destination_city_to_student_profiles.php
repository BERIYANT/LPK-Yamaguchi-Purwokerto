<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        if (! Schema::hasColumn('student_profiles', 'destination_city')) {
            Schema::table('student_profiles', function (Blueprint $table): void {
                $table->string('destination_city', 100)->nullable()->after('placement');
            });
        }
    }

    public function down(): void
    {
        if (Schema::hasColumn('student_profiles', 'destination_city')) {
            Schema::table('student_profiles', function (Blueprint $table): void {
                $table->dropColumn('destination_city');
            });
        }
    }
};
