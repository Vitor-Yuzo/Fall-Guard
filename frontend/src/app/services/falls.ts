import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface FallEvent {
  id: number;
  evento: string;
  classe: string;
  confianca: number | null;
  timestamp_evento: string;
}

@Injectable({
  providedIn: 'root'
})
export class FallsService {
  private http = inject(HttpClient);

  private readonly apiUrl = 'http://127.0.0.1:5000/api/falls';

  getFalls(): Observable<FallEvent[]> {
    return this.http.get<FallEvent[]>(this.apiUrl);
  }
}