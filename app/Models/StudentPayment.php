<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Table;

#[Table('student_payments')]
class StudentPayment extends LegacyModel
{
    public $timestamps = false;
}
