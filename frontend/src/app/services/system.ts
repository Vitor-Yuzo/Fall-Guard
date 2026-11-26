
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface SystemStatus {
  mysql: boolean;
  mqtt: boolean;
  camera_yolo: boolean;
  sistema_ativo: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class SystemService {
  private http = inject(HttpClient);

  private readonly apiUrl = 'http://127.0.0.1:5000/api/system';

  getStatus(): Observable<SystemStatus> {
    return this.http.get<SystemStatus>(`${this.apiUrl}/status`);
  }

  startSystem(): Observable<any> {
    return this.http.post(`${this.apiUrl}/start`, {});
  }

  stopSystem(): Observable<any> {
    return this.http.post(`${this.apiUrl}/stop`, {});
  }
}
