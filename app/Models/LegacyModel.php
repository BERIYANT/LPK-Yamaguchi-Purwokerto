<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

abstract class LegacyModel extends Model
{
    protected $primaryKey = 'id';

    protected $guarded = [];
}
