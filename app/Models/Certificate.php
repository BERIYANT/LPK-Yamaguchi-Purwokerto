<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Table;

#[Table('certificates')]
class Certificate extends LegacyModel
{
    public $timestamps = false;
}
