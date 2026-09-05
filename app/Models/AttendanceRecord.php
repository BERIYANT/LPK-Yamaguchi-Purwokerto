<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Table;

#[Table('attendance_records')]
class AttendanceRecord extends LegacyModel
{
    public $timestamps = false;
}
